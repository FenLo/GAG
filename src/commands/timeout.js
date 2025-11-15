const { SlashCommandBuilder, PermissionFlagsBits } = require('discord.js');
const { logModerationAction } = require('../database');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('timeout')
        .setDescription('Bir kullanıcıyı belirli dakika kadar susturur.')
        .addUserOption(option =>
            option.setName('member')
                .setDescription('Susturulacak kullanıcı')
                .setRequired(true))
        .addIntegerOption(option =>
            option.setName('minutes')
                .setDescription('Susturma süresi (dakika)')
                .setRequired(true)
                .setMinValue(1)
                .setMaxValue(40320))
        .addStringOption(option =>
            option.setName('reason')
                .setDescription('Susturma sebebi')
                .setRequired(false))
        .setDefaultMemberPermissions(PermissionFlagsBits.Administrator),
    async execute(interaction) {
        await interaction.deferReply();

        const member = interaction.options.getMember('member');
        const minutes = interaction.options.getInteger('minutes');
        const reason = interaction.options.getString('reason') || 'Sebep belirtilmedi';

        if (!member) {
            return await interaction.followUp({ content: '❌ Kullanıcı bulunamadı.', ephemeral: true });
        }

        try {
            await member.timeout(minutes * 60 * 1000, reason);
            await interaction.followUp(`🔇 ${member} adlı kullanıcı ${minutes} dakika susturuldu. Sebep: ${reason}`);
            
            logModerationAction(
                interaction.guild.id,
                interaction.guild.name,
                member.id,
                member.displayName,
                interaction.user.id,
                interaction.user.displayName,
                'timeout',
                reason
            );
        } catch (error) {
            console.error('Timeout error:', error);
            await interaction.followUp({ content: '❌ Bu kullanıcıyı susturmak için yetkim yok.', ephemeral: true });
        }
    }
};
