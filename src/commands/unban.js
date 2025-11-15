const { SlashCommandBuilder, PermissionFlagsBits } = require('discord.js');
const { logModerationAction } = require('../database');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('unban')
        .setDescription('Banlanan bir kullanıcının yasağını kaldırır.')
        .addUserOption(option =>
            option.setName('user')
                .setDescription('Yasağı kaldırılacak kullanıcı')
                .setRequired(true))
        .addStringOption(option =>
            option.setName('reason')
                .setDescription('Yasak kaldırma sebebi')
                .setRequired(false))
        .setDefaultMemberPermissions(PermissionFlagsBits.Administrator),
    async execute(interaction) {
        await interaction.deferReply();

        const user = interaction.options.getUser('user');
        const reason = interaction.options.getString('reason') || 'Sebep belirtilmedi';

        try {
            await interaction.guild.members.unban(user.id, reason);
            await interaction.followUp(`✅ ${user.tag} adlı kullanıcının yasağı kaldırıldı. Sebep: ${reason}`);
            
            logModerationAction(
                interaction.guild.id,
                interaction.guild.name,
                user.id,
                user.tag,
                interaction.user.id,
                interaction.user.displayName,
                'unban',
                reason
            );
        } catch (error) {
            console.error('Unban error:', error);
            await interaction.followUp({ content: '❌ Bu kullanıcının yasağını kaldırmak için yetkim yok veya kullanıcı banlı değil.', ephemeral: true });
        }
    }
};
