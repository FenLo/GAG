const { SlashCommandBuilder, PermissionFlagsBits } = require('discord.js');
const { logModerationAction } = require('../database');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('softban')
        .setDescription('Kullanıcıyı softbanlar (banlayıp hemen unbanlar, mesajlarını siler).')
        .addUserOption(option =>
            option.setName('member')
                .setDescription('Softbanlanacak kullanıcı')
                .setRequired(true))
        .addStringOption(option =>
            option.setName('reason')
                .setDescription('Softban sebebi')
                .setRequired(false))
        .setDefaultMemberPermissions(PermissionFlagsBits.BanMembers),
    async execute(interaction) {
        await interaction.deferReply();

        const member = interaction.options.getMember('member');
        const reason = interaction.options.getString('reason') || 'Sebep belirtilmedi';

        if (!member) {
            return await interaction.followUp({ content: '❌ Kullanıcı bulunamadı.', ephemeral: true });
        }

        try {
            await member.ban({ deleteMessageSeconds: 604800, reason });
            await interaction.guild.members.unban(member.id, 'Softban');
            
            await interaction.followUp(`⚠️ ${member.user.tag} softbanlandi (mesajları silindi). Sebep: ${reason}`);
            
            logModerationAction(
                interaction.guild.id,
                interaction.guild.name,
                member.id,
                member.displayName,
                interaction.user.id,
                interaction.user.displayName,
                'softban',
                reason
            );
        } catch (error) {
            console.error('Softban error:', error);
            await interaction.followUp({ content: '❌ Bu kullanıcıyı softbanlamak için yetkim yok.', ephemeral: true });
        }
    }
};
